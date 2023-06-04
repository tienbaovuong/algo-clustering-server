from .health import ping
from .clustering import clustering_routes

def add_routes(routes, routers, tags):
    prefix = '/api/v1/vit'
    for route in routes:
        routers.append({
            'router': route,
            'tags': tags,
            'prefix': prefix
        })

routers = []

routers.append({
    'router': ping.router
})
add_routes(clustering_routes, routers, [])
