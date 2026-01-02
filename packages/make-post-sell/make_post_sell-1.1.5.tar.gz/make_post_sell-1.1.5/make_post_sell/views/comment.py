from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from . import (
    get_referer_or_home,
    user_required,
)

from ..models.comment import (
    Comment,
    get_comment_by_id,
    get_comments_for_product,
)

from ..models.product import get_product_by_id

from ..models.user import get_user_by_id

from ..lib.render import markdown_to_html


@view_config(route_name="comment_new", request_method="POST")
@user_required()
def comment_new(request):
    """Create a new comment."""
    product_id = request.params.get("product_id")
    parent_id = request.params.get("parent_id")  # For replies
    data = request.params.get("data", "").strip()

    if not product_id or not data:
        request.session.flash(("Comment content is required", "error"))
        return HTTPFound(location=get_referer_or_home(request))

    # Get product and validate
    product = get_product_by_id(request.dbsession, product_id)
    if not product:
        return HTTPNotFound("Product not found")

    shop = product.shop

    # Check if user can comment
    can_comment, error_msg = True, None

    if not shop.comments_enabled:
        can_comment, error_msg = False, "Comments are disabled for this shop"
    elif shop.comments_require_purchase:
        # Check if user has purchased this product
        from ..models.user_product import UserProduct

        user_product = (
            request.dbsession.query(UserProduct)
            .filter(
                UserProduct.user_id == request.user.id,
                UserProduct.product_id == product_id,
            )
            .first()
        )

        if not user_product:
            can_comment, error_msg = (
                False,
                "You must purchase this product to leave a comment",
            )

    if not can_comment:
        request.session.flash((error_msg, "error"))
        return HTTPFound(location=get_referer_or_home(request))

    # Create comment
    comment = Comment()
    comment.product_id = product_id
    comment.user_id = request.user.id
    comment.set_data(data)

    # Set approval status based on shop settings
    if shop.comments_require_approval:
        # Shop owners and editors get auto-approved
        if shop.is_owner(request.user) or shop.is_editor(request.user):
            comment.approved = True
        else:
            comment.approved = False
    else:
        # No approval required
        comment.approved = True

    # Handle reply (set parent and root)
    if parent_id:
        parent_comment = get_comment_by_id(request.dbsession, parent_id)
        if parent_comment and parent_comment.product_id == product_id:
            comment.parent_id = parent_id
            comment.root_id = parent_comment.root_id or parent_comment.id
            comment.recompute_depth()
    else:
        # Root comment
        comment.root_id = comment.id
        comment.graph_depth = 0

    request.dbsession.add(comment)
    request.dbsession.flush()

    if comment.approved:
        request.session.flash(("Comment posted successfully", "success"))
    else:
        request.session.flash(("Comment submitted for approval", "success"))

    # Redirect to the product page with fragment to scroll to the new comment
    product_url = product.absolute_url(request)
    return HTTPFound(location=f"{product_url}#comment-{comment.id}")


@view_config(route_name="comment_reply", renderer="comments/reply_comment.j2")
@user_required()
def comment_reply_get(request):
    """Show reply to comment form."""
    comment_id = request.matchdict["comment_id"]
    parent_comment = get_comment_by_id(request.dbsession, comment_id)

    if not parent_comment:
        return HTTPNotFound("Comment not found")

    # Check if user can reply
    shop = parent_comment.product.shop
    can_comment, error_msg = parent_comment.can_user_comment(request.user, shop)

    if not can_comment:
        request.session.flash((error_msg, "error"))
        return HTTPFound(location=parent_comment.product.absolute_url(request))

    return {
        "parent_comment": parent_comment,
        "product": parent_comment.product,
        "shop": shop,
    }


@view_config(route_name="comment_reply", request_method="POST")
@user_required()
def comment_reply_post(request):
    """Create a reply to a comment."""
    comment_id = request.matchdict["comment_id"]
    parent_comment = get_comment_by_id(request.dbsession, comment_id)

    if not parent_comment:
        return HTTPNotFound("Comment not found")

    # Check if user can reply
    shop = parent_comment.product.shop
    can_comment, error_msg = parent_comment.can_user_comment(request.user, shop)

    if not can_comment:
        request.session.flash((error_msg, "error"))
        return HTTPFound(location=parent_comment.product.absolute_url(request))

    data = request.params.get("data", "").strip()

    if not data:
        request.session.flash(("Comment content is required", "error"))
        return HTTPFound(
            location=request.route_url("comment_reply", comment_id=comment_id)
        )

    # Create reply comment
    comment = Comment()
    comment.product_id = parent_comment.product_id
    comment.user_id = request.user.id
    comment.parent_id = parent_comment.id
    comment.root_id = parent_comment.root_id or parent_comment.id
    comment.set_data(data)
    comment.recompute_depth()

    # Set approval status based on shop settings
    if shop.comments_require_approval:
        # Shop owners and editors get auto-approved
        if shop.is_owner(request.user) or shop.is_editor(request.user):
            comment.approved = True
        else:
            comment.approved = False
    else:
        # No approval required
        comment.approved = True

    request.dbsession.add(comment)
    request.dbsession.flush()

    if comment.approved:
        request.session.flash(("Reply posted successfully", "success"))
    else:
        request.session.flash(("Reply submitted for approval", "success"))

    # Redirect to the product page with fragment to scroll to the new comment
    product_url = parent_comment.product.absolute_url(request)
    return HTTPFound(location=f"{product_url}#comment-{comment.id}")


@view_config(route_name="comment_edit", renderer="comments/edit_comment.j2")
@user_required()
def comment_edit_get(request):
    """Show edit comment form."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions
    shop = comment.product.shop
    if comment.user_id != request.user.id and not comment.can_user_moderate(
        request.user, shop
    ):
        return HTTPForbidden("You can only edit your own comments")

    return {
        "comment": comment,
        "product": comment.product,
        "shop": shop,
    }


@view_config(route_name="comment_edit", request_method="POST")
@user_required()
def comment_edit_post(request):
    """Update a comment."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions
    shop = comment.product.shop
    if comment.user_id != request.user.id and not comment.can_user_moderate(
        request.user, shop
    ):
        return HTTPForbidden("You can only edit your own comments")

    data = request.params.get("data", "").strip()

    if not data:
        request.session.flash(("Comment content is required", "error"))
        return HTTPFound(
            location=request.route_url("comment_edit", comment_id=comment_id)
        )

    comment.set_data(data)
    request.session.flash(("Comment updated successfully", "success"))

    # Redirect back to product page with fragment to scroll to the edited comment
    product_url = comment.product.absolute_url(request)
    return HTTPFound(location=f"{product_url}#comment-{comment.id}")


@view_config(route_name="comment_delete", request_method="POST")
@user_required()
def comment_delete(request):
    """Delete a comment."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions
    shop = comment.product.shop
    if comment.user_id != request.user.id and not comment.can_user_moderate(
        request.user, shop
    ):
        return HTTPForbidden("You can only delete your own comments")

    product_url = comment.product.absolute_url(request)

    # Determine which comment to anchor to after deletion
    if comment.parent_id:
        # For replies, anchor to the parent comment
        anchor_comment_id = comment.parent_id
    else:
        # For root comments, just go to the product page
        anchor_comment_id = None

    # Soft delete using disable method
    comment.disable()

    request.session.flash(("Comment deleted successfully", "success"))

    if anchor_comment_id:
        return HTTPFound(location=f"{product_url}#comment-{anchor_comment_id}")
    else:
        return HTTPFound(location=product_url)


@view_config(route_name="comment_approve", request_method="POST")
@user_required()
def comment_approve(request):
    """Approve a comment (shop owners and editors only)."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions - shop owners and editors can approve
    shop = comment.product.shop
    if not comment.can_user_moderate(request.user, shop):
        return HTTPForbidden("Only shop owners and editors can approve comments")

    comment.approved = True
    comment.stamp_updated_timestamp()

    request.session.flash(("Comment approved", "success"))

    # Determine which comment to anchor to after approval
    product_url = comment.product.absolute_url(request)
    if comment.parent_id:
        # For replies, anchor to the parent comment
        return HTTPFound(location=f"{product_url}#comment-{comment.parent_id}")
    else:
        # For root comments, anchor to the comment itself
        return HTTPFound(location=f"{product_url}#comment-{comment.id}")


@view_config(route_name="comment_unapprove", request_method="POST")
@user_required()
def comment_unapprove(request):
    """Unapprove a comment (shop owners and editors only)."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions - shop owners and editors can unapprove
    shop = comment.product.shop
    if not comment.can_user_moderate(request.user, shop):
        return HTTPForbidden("Only shop owners and editors can moderate comments")

    comment.approved = False
    comment.stamp_updated_timestamp()

    request.session.flash(("Comment unapproved", "success"))

    # Determine which comment to anchor to after unapproval
    product_url = comment.product.absolute_url(request)
    if comment.parent_id:
        # For replies, anchor to the parent comment
        return HTTPFound(location=f"{product_url}#comment-{comment.parent_id}")
    else:
        # For root comments, anchor to the comment itself
        return HTTPFound(location=f"{product_url}#comment-{comment.id}")


@view_config(route_name="comment_undelete", request_method="POST")
@user_required()
def comment_undelete(request):
    """Undelete a comment (shop owners and editors only)."""
    comment_id = request.matchdict["comment_id"]
    comment = get_comment_by_id(request.dbsession, comment_id)

    if not comment:
        return HTTPNotFound("Comment not found")

    # Check permissions - comment owner, shop owners, or shop editors can undelete
    shop = comment.product.shop
    if comment.user_id != request.user.uuid_str and not (
        shop.is_owner(request.user) or shop.is_editor(request.user)
    ):
        return HTTPForbidden(
            "Only comment owners, shop owners, and shop editors can undelete comments"
        )

    # Re-enable the comment
    comment.enable()

    request.session.flash(("Comment restored successfully", "success"))
    return HTTPFound(location=comment.product.absolute_url(request))
