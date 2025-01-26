from google.cloud.firestore import AsyncDocumentReference

from model.error import ErrorKind, AppError


async def delete_sub_collections(doc_ref: AsyncDocumentReference) -> None:
    try:
        async for collection in doc_ref.collections():
            async for doc in collection.stream():
                await delete_sub_collections(doc.reference)
                await doc.reference.delete()
    except Exception as e:
        raise AppError(
            ErrorKind.INTERNAL, "サブコレクションの削除に失敗しました。"
        ) from e
