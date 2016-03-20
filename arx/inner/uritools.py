def uridisplay(uri, maskauth=True):
    if maskauth and uri.userinfo is not None:
        net = ':'.join(item for item in [uri.host, uri.port] if item)
        user, found, _ = uri.userinfo.partition(':')
        masked = (user + found if found else '') + '...'
        uri = uri._replace(authority='@'.join([masked, net]))
    return uri.geturi()
