from gwcconfig.GeoWebCacheServer import GeoWebCacheServer
try:
    from config import *
except ImportError:
    print("Failed to load settings")

def main():
    server = GeoWebCacheServer(GWC_REST_API_URL,GWC_REST_API_USERNAME,GWC_REST_API_PASSWORD)
    for layer in server.get_layers():
        print layer

if __name__ == '__main__':
    main()
