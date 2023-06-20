from .health import ping
from .clustering import clustering_routes
from .cluster_history import cluster_history_routes, internal_cluster_history_routes
from .thesis_data import thesis_data_routes, internal_thesis_data_routes

def add_routes(routes, routers, tags, internal: bool = False):
    if internal:
        prefix = '/internal_api/v1'
    else:
        prefix = '/api/v1'
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
add_routes(clustering_routes, routers, [], False)
add_routes(cluster_history_routes, routers, [], False)
add_routes(thesis_data_routes, routers, [], False)

add_routes(internal_thesis_data_routes, routers, [], True)
add_routes(internal_cluster_history_routes, routers, [], True)