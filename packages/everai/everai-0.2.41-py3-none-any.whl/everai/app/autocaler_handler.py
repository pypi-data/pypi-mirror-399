import flask
from flask import Flask, Blueprint

from everai.app.app import App
from everai.app.context import service_context
from everai_autoscaler.model import Factors
from everai_autoscaler.builtin import SimpleAutoScaler


def register_autoscaling_handler(flask_app: Flask, app: App):
    everai_blueprint = Blueprint('everai-autoscaler', __name__, url_prefix='/-everai-')

    @everai_blueprint.route('/autoscaler', methods=['POST'])
    def autoscaling():
        data = flask.request.data

        try:
            factors = Factors.from_json(data)
        except Exception as e:
            return f'Bad request, {e}', 400

        try:
            with service_context(app.runtime.context()):
                autoscaling_policy = app.autoscaler
                if autoscaling_policy is None:
                    autoscaling_policy = SimpleAutoScaler()
                    print('use default SimpleAutoScalingPolicy')

                assert hasattr(autoscaling_policy, 'decide')
                decide = getattr(autoscaling_policy, 'decide')
                assert callable(decide)

                result = decide(factors)
        except Exception as e:
            return f'Internal Server Error, {e}', 500

        return flask.Response(result.json(), mimetype='application/json')

    flask_app.register_blueprint(everai_blueprint)
    print(f'handler is /-everai-/autoscaler')
