# brain/api/__init__.py

from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import json
import logging
import os
from typing import Dict, Any

from ..models import BrainRun, BrainRunEvent
from ..langgraph_flow.graph import ProductRoadmapGraph, create_ai_job_workflow
from ..serializers import BrainRunSerializer

logger = logging.getLogger(__name__)


class StartAIJobView(APIView):
    """
    POST /api/brain/start_job/
    
    Start a new AI job for document processing and roadmap generation.
    Supports file uploads and URL processing with framework selection.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Parse request data
            framework = request.data.get('framework', 'RICE')
            product_context = request.data.get('product_context', '')
            links = request.data.get('links', [])
            
            # Handle links as JSON string or list
            if isinstance(links, str):
                try:
                    links = json.loads(links)
                except json.JSONDecodeError:
                    links = [links] if links else []
            
            # Process uploaded files
            uploaded_files = []
            if 'files' in request.FILES:
                files = request.FILES.getlist('files')
                for file in files:
                    # Save uploaded file
                    file_path = self._save_uploaded_file(file)
                    uploaded_files.append(file_path)
            
            # Validate inputs
            if not uploaded_files and not links:
                return Response({
                    'error': 'No files or links provided for processing'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get organization (for multi-tenant support)
            organization_id = getattr(request.user, 'organization_id', None)
            
            # Create BrainRun
            run = BrainRun.objects.create(
                status='running',
                organization_id=organization_id,
                metadata={
                    'framework': framework,
                    'product_context': product_context,
                    'file_count': len(uploaded_files),
                    'link_count': len(links),
                    'user_id': request.user.id
                }
            )
            
            # Create initial workflow state
            initial_state = create_ai_job_workflow(
                uploaded_files=uploaded_files,
                links=links,
                framework=framework,
                product_context=product_context,
                organization_id=organization_id
            )
            
            # Start processing (for now, just run perception layer)
            try:
                # Initialize the graph
                graph = ProductRoadmapGraph()
                
                # Run the workflow
                final_state = graph.run_workflow(run, initial_state)
                
                # Mark run as completed
                run.status = 'completed'
                run.save()
                
                # Return response with job details
                parsed_docs = final_state.parsed_documents or []
                return Response({
                    'job_id': run.id,
                    'status': 'completed',
                    'message': 'AI job completed successfully',
                    'results': {
                        'documents_processed': len(parsed_docs),
                        'successful_documents': sum(1 for doc in parsed_docs if doc.validation_result.is_valid),
                        'framework': framework,
                        'processing_summary': self._create_processing_summary(final_state)
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                # Mark run as failed
                run.mark_failed('processing_error', str(e))
                
                logger.error(f"AI job processing failed for run {run.id}: {e}", exc_info=True)
                
                return Response({
                    'job_id': run.id,
                    'status': 'failed',
                    'error': f'Processing failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Failed to start AI job: {e}", exc_info=True)
            return Response({
                'error': f'Failed to start job: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _save_uploaded_file(self, file) -> str:
        """Save uploaded file and return the file path."""
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join('media', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        filename = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        return file_path
    
    def _create_processing_summary(self, state) -> Dict[str, Any]:
        """Create a summary of processing results."""
        if not state.parsed_documents:
            return {'message': 'No documents processed'}
        
        total_content_length = sum(len(doc.content) for doc in state.parsed_documents)
        total_tables = sum(len(doc.tables) for doc in state.parsed_documents)
        file_types = list(set(doc.file_type for doc in state.parsed_documents))
        
        return {
            'total_content_length': total_content_length,
            'total_tables': total_tables,
            'file_types': file_types,
            'average_quality_score': sum(doc.validation_result.quality_score for doc in state.parsed_documents) / len(state.parsed_documents)
        }


class JobStatusView(APIView):
    """
    GET /api/brain/job/{job_id}/status/
    
    Get the status of an AI job.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        try:
            run = BrainRun.objects.get(id=job_id)
            
            # Check permission (basic organization check)
            if hasattr(request.user, 'organization_id') and run.organization.id != request.user.organization_id:
                return Response({
                    'error': 'Job not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = BrainRunSerializer(run)
            return Response(serializer.data)
            
        except BrainRun.DoesNotExist:
            return Response({
                'error': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class JobTraceView(APIView):
    """
    GET /api/brain/job/{job_id}/trace/
    
    Get detailed execution trace for an AI job.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id):
        try:
            run = BrainRun.objects.get(id=job_id)
            
            # Check permission
            if hasattr(request.user, 'organization_id') and run.organization.id != request.user.organization_id:
                return Response({
                    'error': 'Job not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get all events for this run
            events = BrainRunEvent.objects.filter(run=run).order_by('created_at')
            
            trace_data = {
                'job_id': run.id,
                'status': run.status,
                'created_at': run.created_at,
                'updated_at': run.updated_at,
                'metadata': run.meta,
                'events': []
            }
            
            for event in events:
                trace_data['events'].append({
                    'event_type': event.event_type,
                    'data': event.payload,
                    'created_at': event.created_at
                })
            
            return Response(trace_data)
            
        except BrainRun.DoesNotExist:
            return Response({
                'error': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)


# URL patterns for these views
ai_job_urlpatterns = [
    path('start_job/', StartAIJobView.as_view(), name='start_ai_job'),
    path('job/<int:job_id>/status/', JobStatusView.as_view(), name='job_status'),
    path('job/<int:job_id>/trace/', JobTraceView.as_view(), name='job_trace'),
]
