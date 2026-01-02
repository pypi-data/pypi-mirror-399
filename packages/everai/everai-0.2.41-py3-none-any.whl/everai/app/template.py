
_template = """
version: everai/v1alpha1
kind: App
metadata:
  name: manifest-example                          # *application name, required field
  namespace: some-namespace                       # default is default
spec:
  image: quay.io/mc_jones/get-start:v0.0.30       # *image for serverless app, required field
  imagePullSecrets:                               # image pull secrets, optional when use a public image
    username:                                     # username for docker registry
      valueFrom:                                  # reference from secret
        secretKeyRef:
          name: quay-secret
          key: username
      # value: foo                                # plain text is supported
    password:                                     # password for docker registry, reference from secret quay-secret
      valueFrom:
        secretKeyRef:
          name: quay-secret
          key: password
  volumeMounts:                                   # optional volume mounts
    - name: sd                                    # name
      mountPath: /models/stable-diffusion-3       # mount path in container
      readOnly: true                              # only support `readOnly = true` currently, default is true
    - name: pv
      mountPath: /models/private-volume
    - name: quay
      mountPath: /secrets/quay
    - name: test-configmap
      mountPath: /configmaps/test-configmap

  env:                                            # optional environment variables
    - name: T1                                    # set T1=test
      value: test                                   
    - name: HUGGINGFACE_TOKEN                     # set HUGGINGFACE_TOKEN from secret huggingface-token.key
      valueFrom:
        secretKeyRef:
          name: huggingface-token
          key: token
    - name: RECHECK_INTERVAL                      # set RECHECK_INTERVAL from configmap app-configmap.recheck-interval
      valueFrom:
        configMapKeyRef:
          name: app-configmap
          key: recheck-interval

  command:                                        # optional command 
    - /entrypoint.sh
    - listen
    - :80
  port: 80                                        # just one port cloud be set, everai will pass any http request /**
                                                  # to this port, default is 80
  readinessProbe:                                 # if readinessProbe is set up, there are no any request be route
                                                  # to this worker before probe status is ready ( status code = 200 ),
                                                  # otherwise (readinessProbe is not set up), everai will route reqeust
                                                  # to this worker when container is ready,
                                                  # even model not loaded into memory of gpu
    httpGet:                                      # http get is only supported methods now
      path: /-everai-/healthy                     # only http status 200 means ready

  volumes:                                        # optional field, but very important for AI app
    - name: sd                                    # volume name
      volume: expvent/stable-diffusion-3          # use a public volume from other user
    - name: pv                                    # volume name
      volume: private-volume                      # use a private volume

    - name: quay
      secret:                                     # volume from secret
        secretName: quay-secret                   # secret name, every key as a file name in mount path
                                                  # or set items for specific key
    - name: test-configmap
      configMap:                                  # volume from configMap
        name: test-configmap
        items:
          - key: k1                               # k1 as file name p1 be placed into mount path
            path: p1

    # if container use everai library to build your app,
    # you can just define your secret and configmap requirements in volumes and without any volumeMounts
    # just like in app.py set
    #     secret_requests=[QUAY_IO_SECRET_NAME],
    #     configmap_requests=[CONFIGMAP_NAME],

  resources:                                      # *resource request, required
    cpu: 2                                        # *cpu number
    memory: 2 GiB                                 # *memory size, for example, "1024 MiB", "10 GiB", "20480 MiB"
    gpu: 1                                        # gpu number, default is 0
    filters:
      gpu: ["A100 40G", "4090"]                   # gpu type constraints, more information at everai.expvent.com
                                                  # or use everai commandline tools query, everai resources --gpus
      cpu: []                                     # cpu type constraints, more information at everai.expvent.com
                                                  # or use everai commandline tools query, everai resources --cpus
      regions: []                                 # region constraints, more information at everai.expvent.com
                                                  # or use everai commandline tools query, everai resources --regions
                                                  # empty list means every region satisfies requirements
      cuda: ""                                    # cuda version constraints, like version ">=x.x.x"
      nvidia: ""                                  # nvidia driver version constraints, like version ">=x.x.x"
"""


def template() -> str:
    return _template
