# ===================================================using tessaract==============================
# import pytesseract
# from rest_framework.parsers import FormParser
# from rest_framework.parsers import MultiPartParser
# from .serializers import UploadedFileSerializer
# from rest_framework.generics import CreateAPIView
#
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# # extract .pdf,xl,csv,jpg,png,docx,py,
# class Uploaded_File(CreateAPIView):
#     serializer_class = UploadedFileSerializer
#     parser_classes = (MultiPartParser, FormParser)
#
#     def post(self, request, *args, **kwargs):
#         try:
#             # Create and validate the serializer
#             serializer = UploadedFileSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#
#             uploaded_files = UploadedFile.objects.filter(id=serializer.data['id'])
#             interact = uploaded_files.first()
#             pdf_files = [interact.file_upload.path]
#             for file_path in pdf_files:
#                 loader = UnstructuredFileLoader(file_path)
#                 docs = loader.load()
#                 text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#                 document = text_splitter.split_documents(docs)
#                 embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#                 db = FAISS.from_documents(document, embeddings)
#                 db.save_local('attachment')
#                 os.remove(file_path)
#                 return HttpResponse(docs[0].page_content[:])
#
#             print('successfully loaded')
#
#         except Exception as e:
#             return HttpResponse(str(e))

# ===============================================unstructured file loader=================================

import os
from langchain.document_loaders import UnstructuredFileLoader, UnstructuredXMLLoader, UnstructuredEmailLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from rest_framework.parsers import FormParser, MultiPartParser
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from rest_framework.generics import CreateAPIView
from django.http import HttpResponse
import json


class Uploaded_File( CreateAPIView ):
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # global path, docs
        try:
            serializer = UploadedFileSerializer( data=request.data )
            serializer.is_valid( raise_exception=True )
            serializer.save()
            uploaded_files = UploadedFile.objects.filter( id=serializer.data['id'] )
            interact = uploaded_files.first()
            file_path = [interact.file_upload.path]

            for path_file in file_path:
                file_name = os.path.basename( path_file )

                if file_name.endswith( '.json' ):
                    with open( path_file ) as json_file:
                        docs = json.load( json_file )
                elif file_name.endswith( '.xml' ):
                    loader = UnstructuredXMLLoader( path_file )
                    docs = loader.load()
                else:
                    loader = UnstructuredFileLoader( path_file )
                    docs = loader.load()

                if file_name.endswith( '.json' ):
                    text_splitter = CharacterTextSplitter( chunk_size=1000, chunk_overlap=0 )
                    document = text_splitter.create_documents( docs )
                else:
                    text_splitter = CharacterTextSplitter( chunk_size=1000, chunk_overlap=0 )
                    document = text_splitter.split_documents( docs )

                embeddings = HuggingFaceEmbeddings( model_name="all-MiniLM-L6-v2" )
                db = FAISS.from_documents( document, embeddings )
                db.save_local( 'attachment' )
                os.remove( path_file )
                print(docs)
                return HttpResponse( docs)

        except Exception as e:
            return HttpResponse( str( e ) )
