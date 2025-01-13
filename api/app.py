from typing import Union

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File

from argparse import ArgumentParser

from fastapi.responses import JSONResponse
from lib.wormpicker.module_crs_converter import trans4mEPSG
from lib.wormpicker.Objects import *
from lib.wormpicker.UserCred import saveCredentials
from lib.wormpicker.GetLayers_Window import getLayers
from lib.wormpicker.functions import *
import re
import os
import pandas as pd
from tempfile import NamedTemporaryFile


app = FastAPI()


@app.get("/api/test")
def test():
    return {"test": "success"}


@app.post("/api/wormpicker")
def wormpicker(file: UploadFile = File(...)):

    try:

        log_object = LogObject()

        with NamedTemporaryFile(delete=True, suffix=".csv") as temp_file:
            contents = file.file.read()
            temp_file.write(contents)
            temp_file.seek(0)
            samples = temp_file.name

            logger = log_object.logger
            username = None
            password = None
            endpoint = None

            layer_info = getLayers(savepath="NONE",
                                   rasdaman_endpoint=endpoint,
                                   rasdaman_password=password,
                                   rasdaman_username=username,
                                   loggerobject=logger)

            x = Coverage(layer_info)
            x.getBoundary()
            x.getSamples(samples)
            samplescovered = x.samples

            layers_to_analyze = select_objects("automatic", x)
            info = layer_info[0]

            layerlist = []
            for layer in layers_to_analyze:
                for i in range(0, len(x._data)):
                    entries_list = list(x._data[i])
                    try:
                        index = entries_list.index(layer)
                        layerlist.append(entries_list)
                    except:
                        continue

            header_list, values_list = requestDataWGS(info, layerlist, samplescovered, filepath="NONE", offset=0, approximate=True, rasdaman_password=password, rasdaman_username=username, rasdaman_endpoint=endpoint, loggerobject=logger)

            df = pd.DataFrame(data=values_list, columns=header_list)
            log = list(map(lambda p: {"time": p[0], "type": p[1], "log": p[2]}, map(lambda p: p.split(" - "), log_object.get_logs())))

            return {"log": log, "result": df.to_dict("records")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
