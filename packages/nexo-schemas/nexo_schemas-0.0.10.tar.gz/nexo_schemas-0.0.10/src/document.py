import csv
from io import StringIO
from fastapi import UploadFile
from pydantic import BaseModel, Field, PrivateAttr, computed_field, model_validator
from typing import Annotated, ClassVar, Generic, Self, TypeVar
from nexo.types.integer import OptInt
from nexo.types.string import OptStr, OptStrT, SeqOfStrs
from .error.enums import ErrorCode


class Document(BaseModel):
    _raw: UploadFile | None = PrivateAttr(None)
    content: Annotated[bytes, Field(..., description="Content", exclude=True)]
    content_type: Annotated[str, Field(..., description="Content Type")]
    filename: Annotated[str, Field(..., description="Filename")]
    size: Annotated[int, Field(..., description="Size", gt=0)]

    @classmethod
    async def from_file(
        cls,
        file: UploadFile,
        *,
        max_size: OptInt = None,
        valid_content_types: SeqOfStrs | str | None = None,
        valid_extensions: SeqOfStrs | str | None = None,
    ) -> Self:
        content = await file.read()
        if not content:
            raise ValueError(ErrorCode.BAD_REQUEST, "Content can not be empty")

        size = file.size
        if size is None or size <= 0:
            raise ValueError(
                ErrorCode.BAD_REQUEST, "Size can not be None and must be larger than 0"
            )
        if max_size is not None:
            if size > max_size:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    f"Size of {size} exceeds set maximum of {max_size}",
                )

        content_type = file.content_type
        if content_type is None:
            raise ValueError("Content type can not be None")
        if valid_content_types is not None:
            if isinstance(valid_content_types, str):
                if content_type != valid_content_types:
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        f"Invalid content type of '{content_type}'. Must be '{valid_content_types}'",
                    )
            else:
                if content_type not in valid_content_types:
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        f"Invalid content type of '{content_type}'. Must be one of {valid_content_types}",
                    )

        filename = file.filename
        if filename is None:
            raise ValueError("Filename can not be None")
        if valid_extensions is not None:
            if isinstance(valid_extensions, str):
                if not filename.endswith(valid_extensions):
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        f"Invalid extension. Must be '{valid_extensions}'",
                    )
            else:
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        f"Invalid extension. Must be one of {valid_extensions}",
                    )

        filename = filename.replace(" ", "_")

        document = cls(
            content=content, content_type=content_type, filename=filename, size=size
        )
        document._raw = file

        return document


class CSVDocument(Document):
    _content_type: ClassVar[str] = "text/csv"

    def _validate_content_type(self):
        if self.content_type != self._content_type:
            raise TypeError(
                ErrorCode.BAD_REQUEST,
                f"CSV Document content type must be {self._content_type}",
            )

    @model_validator(mode="after")
    def validate_content_type(self) -> Self:
        self._validate_content_type()
        return self

    @classmethod
    def from_document(cls, document: Document) -> Self:
        csv_document = cls(
            content=document.content,
            content_type=document.content_type,
            filename=document.filename,
            size=document.size,
        )
        csv_document._raw = document._raw
        return csv_document

    @classmethod
    async def from_file(
        cls,
        file: UploadFile,
        *,
        max_size: OptInt = None,
        valid_content_types: SeqOfStrs | str | None = "text/csv",
        valid_extensions: SeqOfStrs | str | None = ".csv",
    ) -> Self:
        return await super().from_file(
            file,
            max_size=max_size,
            valid_content_types=valid_content_types,
            valid_extensions=valid_extensions,
        )

    def _validate_no_duplicate_rows(self, rows: list[dict[str, OptStr]]) -> None:
        seen = set()
        for index, row in enumerate(rows):
            row_tuple = tuple(sorted(row.items()))
            if row_tuple in seen:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    f"Duplicate row found at index {index}: {row}",
                )
            seen.add(row_tuple)

    @computed_field
    @property
    def rows(self) -> list[dict[str, OptStr]]:
        self._validate_content_type()
        text = self.content.decode(encoding="utf-8-sig")
        reader = csv.DictReader(StringIO(text), skipinitialspace=True)
        raw_rows = list(reader)
        new_rows: list[dict[str, OptStr]] = []

        for row in raw_rows:
            cleaned: dict[str, OptStr] = {}
            for key, value in row.items():
                cleaned[key] = value.strip() if value else None
            new_rows.append(cleaned)

        # Run duplicate validation here
        self._validate_no_duplicate_rows(new_rows)

        return new_rows


class PDFDocument(Document):
    _content_type: ClassVar[str] = "application/pdf"

    def _validate_content_type(self):
        if self.content_type != self._content_type:
            raise TypeError(f"PDF Document content type must be {self._content_type}")

    @model_validator(mode="after")
    def validate_content_type(self) -> Self:
        self._validate_content_type()
        return self

    @classmethod
    def from_document(cls, document: Document) -> Self:
        pdf_document = cls(
            content=document.content,
            content_type=document.content_type,
            filename=document.filename,
            size=document.size,
        )
        pdf_document._raw = document._raw
        return pdf_document

    @classmethod
    async def from_file(
        cls,
        file: UploadFile,
        *,
        max_size: OptInt = None,
        valid_content_types: SeqOfStrs | str | None = "application/pdf",
        valid_extensions: SeqOfStrs | str | None = ".pdf",
    ) -> Self:
        return await super().from_file(
            file,
            max_size=max_size,
            valid_content_types=valid_content_types,
            valid_extensions=valid_extensions,
        )


DocumentT = TypeVar("DocumentT", bound=Document)
OptDocument = Document | None
OptDocumentT = TypeVar("OptDocumentT", bound=OptDocument)
ListOfDocuments = list[Document]
ListOfDocumentsT = TypeVar("ListOfDocumentsT", bound=ListOfDocuments)
OptListOfDocuments = ListOfDocuments | None
OptListOfDocumentsT = TypeVar("OptListOfDocumentsT", bound=OptListOfDocuments)


class DocumentMixin(BaseModel, Generic[OptDocumentT]):
    document: Annotated[OptDocumentT, Field(..., description="Document")]


class HeterogenousDocumentsMixin(BaseModel, Generic[OptListOfDocumentsT]):
    documents: Annotated[
        OptListOfDocumentsT, Field(..., description="Documents", min_length=1)
    ]


class HomogenousDocumentsMixin(BaseModel, Generic[DocumentT]):
    documents: Annotated[
        list[DocumentT], Field(..., description="Documents", min_length=1)
    ]


class OptHomogenousDocumentsMixin(BaseModel, Generic[DocumentT]):
    documents: Annotated[
        list[DocumentT] | None, Field(None, description="Documents", min_length=1)
    ] = None


class DocumentName(BaseModel, Generic[OptStrT]):
    document_name: Annotated[OptStrT, Field(..., description="Document's name")]


class DocumentURL(BaseModel, Generic[OptStrT]):
    document_url: Annotated[OptStrT, Field(..., description="Document's URL")]
