import json
from watson_developer_cloud import VisualRecognitionV3

visual_recognition = VisualRecognitionV3(
    '2018-03-19',
    iam_apikey='4N-WUNUf1xGKkd7PLtp9jp9KU5NmqM5mn1C9DMJd4OaL')

with open('./anu.jpg', 'rb') as images_file:
    classes1 = visual_recognition.classify(
        images_file,
        threshold='0.6',
	classifier_ids='PoojithaKonatham_382182994').get_result()
print(type(classes1))
print(json.dumps(classes1, indent=2))
print(classes1["images"][0]["classifiers"][0]["classes"][0])
a=classes1["images"][0]["classifiers"][0]["classes"][0]["class"]
b=classes1["images"][0]["classifiers"][0]["classes"][0]["score"]
print(a)
print(b)
print(a+ " is waiting at your door")






"""<class 'dict'>
{
  "images": [
    {
      "classifiers": [
        {
          "classifier_id": "PoojithaKonatham_382182994",
          "name": "PoojithaKonatham",
          "classes": [
            {
              "class": "Anupamaparameswaran",
              "score": 0.879
            }
          ]
        }
      ],
      "image": "anu.jpg"
    }
  ],
  "images_processed": 1,
  "custom_classes": 6
}
{'class': 'Anupamaparameswaran', 'score': 0.879}
Anupamaparameswaran
0.879
Anupamaparameswaran is waiting at your door"""
