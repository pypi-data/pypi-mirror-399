from .api_view import APIView
from ..serializers import Serializer
from ..web.response import Response

class GenericAPIView(APIView):
    queryset = None
    serializer_class = None
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.queryset is None:
            raise ValueError('queryset must be set')
        return self.queryset
    
    def get_serializer_class(self):
        if self.serializer_class is None:
            raise ValueError('serializer_class must be set')
        return self.serializer_class
    
    async def get_object(self, request):
        lookup_value = request.path_params.get(self.lookup_field)
        queryset = self.get_queryset()
        return await queryset.get(**{self.lookup_field: lookup_value})
    
    async def get(self, request):
        """获取单个对象或多个对象"""
        if hasattr(request.path_params, self.lookup_field):
            obj = await self.get_object(request)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(obj)
            return Response(serializer.data)
        else:
            queryset = self.get_queryset()
            objects = await queryset.all()
            serializer_class = self.get_serializer_class()
            data = []
            for obj in objects:
                serializer = serializer_class(obj)
                data.append(serializer.data)
            return Response(data)
    
    async def post(self, request):
        serializer_class = self.get_serializer_class()
        data = await request.json()
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            instance = await serializer.save()
            serializer = serializer_class(instance)
            return Response(serializer.data, status_code=201)
        return Response({'errors': serializer.errors}, status_code=400)
    
    async def put(self, request):
        obj = await self.get_object(request)
        serializer_class = self.get_serializer_class()
        data = await request.json()
        serializer = serializer_class(obj, data=data)
        if serializer.is_valid():
            instance = await serializer.save()
            serializer = serializer_class(instance)
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status_code=400)
    
    async def patch(self, request):
        obj = await self.get_object(request)
        serializer_class = self.get_serializer_class()
        data = await request.json()
        serializer = serializer_class(obj, data=data, partial=True)
        if serializer.is_valid():
            instance = await serializer.save()
            serializer = serializer_class(instance)
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status_code=400)
    
    async def delete(self, request):
        obj = await self.get_object(request)
        await obj.delete()
        return Response(status_code=204)

