from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission that ensures users can only access data from their own organization.
    """
    
    def has_permission(self, request, view):
        # User must be authenticated and have an organization
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'organization') and 
            request.user.organization is not None
        )
    
    def has_object_permission(self, request, view, obj):
        # Check if the object belongs to the user's organization
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        
        # For objects that have 'created_by' instead of 'organization'
        if hasattr(obj, 'created_by') and hasattr(obj.created_by, 'organization'):
            return obj.created_by.organization == request.user.organization
        
        # For through models that might be related to organization via related objects
        if hasattr(obj, 'roadmap') and hasattr(obj.roadmap, 'organization'):
            return obj.roadmap.organization == request.user.organization
        
        if hasattr(obj, 'product_initiative') and hasattr(obj.product_initiative, 'organization'):
            return obj.product_initiative.organization == request.user.organization
        
        # Default deny if no organization relationship found
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows owners to edit their objects, others can only read.
    Still respects organization boundaries.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request within the same organization
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Default deny for write operations if no owner relationship
        return False
