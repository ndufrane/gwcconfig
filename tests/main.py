from gwcconfig.GeoWebCacheServer import GeoWebCacheServer
try:
    from config import *
except ImportError:
    print("Failed to load settings")

def main():
    server = GeoWebCacheServer(GWC_REST_API_URL,GWC_REST_API_USERNAME,GWC_REST_API_PASSWORD)

    test_layer = server.get_layer(LAYER_NAME)
    test_layer.fetch()
    test_layer.expireCache =  604900
    for gsu in test_layer.gridSubsets:
        print gsu.gridSetName, gsu.extent_coords
    print test_layer.message()
    server.update(test_layer)

if __name__ == '__main__':
    main()
