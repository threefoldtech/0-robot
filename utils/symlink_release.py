from jumpscale import j

FLIST_HASH = "1cef7d9d4b"
VERSION = "0.9.1"

iyo = j.clients.itsyouonline.get()
jwt = iyo.jwt_get(scope="user:memberof:tf-official-apps")
data = {"token_": jwt, "username": "tf-official-apps", "url": "https://hub.grid.tf/api"}

j.clients.zhub.delete("official-apps")
hub = j.clients.zhub.get("official-apps", data=data, interactive=False)
hub.authenticate()
hub.api.set_user("tf-official-apps")

source = "threefoldtech-0-robot-master-%s.flist" % FLIST_HASH
destination = "threefoldtech-0-robot-%s.flist" % VERSION
print("promote %s to %s" % (source, destination))
hub.promote("tf-autobuilder", source, destination)

source = "threefoldtech-0-robot-autostart-master-%s.flist" % FLIST_HASH
destination = "threefoldtech-0-robot-autostart-%s.flist" % VERSION
print("promote %s to %s" % (source, destination))
hub.promote("tf-autobuilder", source, destination)

source = "threefoldtech-0-robot-%s.flist" % VERSION
destination = "threefoldtech-0-robot-latest.flist"
hub.symlink(source, destination)

source = "threefoldtech-0-robot-autostart-%s.flist" % VERSION
destination = "threefoldtech-0-robot-autostart-latest.flist"
print("symlink %s to %s" % (source, destination))
hub.symlink(source, destination)
