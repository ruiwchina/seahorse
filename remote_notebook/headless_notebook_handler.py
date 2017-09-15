# Copyright (c) 2016, CodiLime Inc.


import os
from nbconvert.exporters.export import exporter_map
from nbconvert.writers.files import FilesWriter
from nbconvert.preprocessors import ExecutePreprocessor
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join
from tornado import web, escape
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python2

from seahorse_notebook_path import SeahorseNotebookPath


class HeadlessNotebookHandler(IPythonHandler):
    executor = ThreadPoolExecutor(max_workers=10)

    @run_on_executor
    def process_notebook(self, path):
        Exporter = exporter_map["html"]
        exporter = Exporter(config=self.config, log=self.log)
        serialized_path = path.serialize()

        # We get ExecutePreprocessor from exporter list
        # and add notebook path so kernel can use the path for various operations.
        # For example it can load the notebook from url
        ep = next(filter(lambda c: isinstance(c, ExecutePreprocessor), exporter._preprocessors))
        ep.extra_arguments.append("--seahorse_notebook_path=" + serialized_path)

        model = self.contents_manager.get(path=serialized_path)
        try:
            output, resources = exporter.from_notebook_node(model['content'])

            model['content'] = resources["seahorse_notebook_content"]
            self.contents_manager.save(model, path=serialized_path)

            resources['output_extension'] = ''
            FilesWriter(config=self.config, log=self.log).write(
                output, resources,
                notebook_name=HeadlessNotebookHandler.notebook_name(path.workflow_id, path.node_id))
        except Exception as e:
            raise web.HTTPError(500, "nbconvert failed: %s" % e)

    def post(self):
        data = escape.json_decode(self.request.body)
        workflow_id, node_id, language = data["workflow_id"], data["node_id"], data["language"]
        try:
            os.remove(self.notebook_name(workflow_id, node_id))
        except FileNotFoundError:
            pass

        # use input dataframe for headless
        seahorse_notebook_path = SeahorseNotebookPath(workflow_id, node_id, language, node_id, 0)
        self.process_notebook(seahorse_notebook_path)
        raise web.HTTPError(202)

    @staticmethod
    def notebook_storage_folder():
        return "/home/jovyan/work/"

    @staticmethod
    def notebook_name(workflow_id, node_id):
        return "{0}{1}_{2}.html".format(
            HeadlessNotebookHandler.notebook_storage_folder(), workflow_id, node_id)

def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    base_url = web_app.settings['base_url']
    route_pattern = url_path_join(base_url, '/HeadlessNotebook')
    web_app.add_handlers(host_pattern, [(route_pattern, HeadlessNotebookHandler)])
    route_pattern_with_workflow_id = url_path_join(base_url, '/HeadlessNotebook/([^/]+)')
    web_app.add_handlers(host_pattern,
                         [(route_pattern_with_workflow_id, web.StaticFileHandler, {"path": "/home/jovyan/work/"})])