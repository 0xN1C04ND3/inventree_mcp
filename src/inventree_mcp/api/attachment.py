"""File attachment management operations for InvenTree."""

from ..utils import _json


async def attachment_operations(
    client,
    operation: str,
    model_type: str = None,
    model_id: int = None,
    attachment_id: int = None,
    file_path: str = None,
    link: str = None,
    comment: str = "",
    destination: str = None,
) -> str:
    """Execute attachment operations.

    Args:
        client: InvenTree client instance
        operation: Operation name
        model_type: Object type (part, stockitem, build, purchaseorder, salesorder, company)
        model_id: Object ID for list/upload/upload_link
        attachment_id: Attachment ID for download/delete
        file_path: Local file path for upload
        link: URL for upload_link
        comment: Optional comment for uploads
        destination: File path to save downloaded attachment to

    Returns:
        JSON string with result or error
    """
    if operation == "list":
        return _json(await client.attachment_list(model_type, model_id))

    elif operation == "upload":
        return _json(
            await client.attachment_upload(model_type, model_id, file_path, comment)
        )

    elif operation == "upload_link":
        return _json(
            await client.attachment_upload_link(model_type, model_id, link, comment)
        )

    elif operation == "download":
        return _json(await client.attachment_download(attachment_id, destination))

    elif operation == "delete":
        return _json(await client.attachment_delete(attachment_id))

    else:
        return _json({"error": f"Unknown operation: {operation}"})
