from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )


class IsAuthenticatedFilterFavoritedAndShoppingCart(BasePermission):
    def has_permission(self, request, view):
        return (
            'is_favorited' not in request.GET.urlencode()
            and 'is_in_shopping_cart' not in request.GET.urlencode()
            or request.user.is_authenticated
        )
