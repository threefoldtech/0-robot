def input(job):
    r = job.service.aysrepo

    # think node can never be argument
    # if "node" in job.model.args and job.model.args["os"] == "":
    #     res = job.model.args
    #     res["os"] = res["node"]
    #     res.pop("node")
    #     job.model.args = res

    if not "device.name" in job.model.args or job.model.args["device.name"].strip() == "":
        res = job.model.args
        res["device.name"] = job.service.model.name
        job.model.args = res

    return job.model.args
