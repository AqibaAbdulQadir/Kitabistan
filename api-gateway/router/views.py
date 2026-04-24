from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests


@method_decorator(csrf_exempt, name='dispatch')
class GatewayView(View):
    SERVICE_URLS = {
        'auth': 'http://user-service:8001',
        'cart': 'http://cart-service:8002',
        'orders': 'http://order-service:8003',
        'books': 'http://product-service:8004',
        'categories': 'http://product-service:8004',
        'payments': 'http://payment-service:8005',
    }

    def _cors(self, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    def options(self, request, path=None):
        return self._cors(HttpResponse('OK'))

    def _forward(self, request, service_name):
        if service_name not in self.SERVICE_URLS:
            return self._cors(JsonResponse({'error': 'Service not found'}, status=404))

        base_url = self.SERVICE_URLS[service_name]
        path = request.path
        query = request.META.get('QUERY_STRING', '')
        url = f"{base_url}{path}"
        if query:
            url += f"?{query}"

        headers = {}
        auth = request.headers.get('Authorization')
        if auth:
            headers['Authorization'] = auth
        headers['Content-Type'] = request.headers.get('Content-Type', 'application/json')

        try:
            method = request.method.lower()
            if method == 'get':
                resp = requests.get(url, headers=headers, timeout=10)
            elif method == 'post':
                resp = requests.post(url, data=request.body, headers=headers, timeout=10)
            elif method == 'put':
                resp = requests.put(url, data=request.body, headers=headers, timeout=10)
            elif method == 'patch':
                resp = requests.patch(url, data=request.body, headers=headers, timeout=10)
            elif method == 'delete':
                resp = requests.delete(url, headers=headers, timeout=10)
            else:
                return self._cors(JsonResponse({'error': 'Method not allowed'}, status=405))

            try:
                return self._cors(JsonResponse(resp.json(), status=resp.status_code, safe=False))
            except:
                return self._cors(JsonResponse({'raw': resp.text[:200]}, status=resp.status_code))

        except requests.exceptions.ConnectionError:
            return self._cors(JsonResponse({'error': f'{service_name} service unavailable'}, status=503))

    def get(self, request, path=None):
        if request.path == '/api/' or request.path == '/api':
            return self._cors(JsonResponse({
                'service': 'Distributed Bookstore API',
                'endpoints': {
                    'health': '/api/health/',
                    'auth': '/api/auth/',
                    'books': '/api/books/',
                    'categories': '/api/categories/',
                    'cart': '/api/cart/',
                    'orders': '/api/orders/',
                    'payments': '/api/payments/',
                }
            }))
        if request.path == '/api/health/':
            return self._cors(JsonResponse({
                'service': 'api-gateway',
                'services': list(self.SERVICE_URLS.keys())
            }))
        service = request.path.strip('/').split('/')[1] if len(request.path.strip('/').split('/')) > 1 else None
        if not service:
            return self._cors(JsonResponse({'error': 'Invalid path'}, status=400))
        return self._forward(request, service)

    def post(self, request, path=None):
        service = request.path.strip('/').split('/')[1] if len(request.path.strip('/').split('/')) > 1 else None
        return self._forward(request, service)

    def put(self, request, path=None):
        service = request.path.strip('/').split('/')[1] if len(request.path.strip('/').split('/')) > 1 else None
        return self._forward(request, service)

    def patch(self, request, path=None):
        service = request.path.strip('/').split('/')[1] if len(request.path.strip('/').split('/')) > 1 else None
        return self._forward(request, service)

    def delete(self, request, path=None):
        service = request.path.strip('/').split('/')[1] if len(request.path.strip('/').split('/')) > 1 else None
        return self._forward(request, service)