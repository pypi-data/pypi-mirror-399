# label-studio-paddleocr

This project integrates [Label Studio](https://labelstud.io/) with [PaddleOCR-VL](https://www.paddleocr.ai/) for OCR and auto labeling.

## Usage

* Deploy PaddleOCR-VL as standalone service. Tutorials can be found at https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/PaddleOCR-VL.html#4-service-deployment
* Create `app.yaml` file as following and run this application. E.g.: `gunicorn label_studio_paddleocr._wsgi:app`.

```yaml
paddleocr_url: http://paddleocr.addr:8080/
label_studio_url: https://labelstudio.addr/
label_studio_api_key: "api token"
```

We have to use Label Studio legacy token instead of personal access token due to https://github.com/HumanSignal/label-studio-ml-backend/issues/749.

* In Label Studio, configure project labeling interface as something like below. Then connect the project with this application in "Model" settings.

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="category" toName="image">
    <Label value="OCR:" background="green" selected="true"/>
    <Label value="Table Recognition:" background="blue"/>
    <Label value="Formula Recognition:" background="red"/>
    <Label value="Chart Recognition:" background="coral"/>
  </RectangleLabels>
  <TextArea name="transcription" toName="image"
            editable="true"
            perRegion="true"
            required="true"
            maxSubmissions="1"
            rows="5"
            placeholder="Recognized Text"
            displayMode="region-list"
            />
</View>
```

