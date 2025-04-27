import { listItem } from "../../../../listItem";

/**
 * This class is responsible for creating and positioning grid content items based on a specified prefab and item count. It instantiates the items and arranges them vertically with a specified offset.
 */

type qapair = {
  question: string;
  answer: string;
};

@component
export class GridContentCreator extends BaseScriptComponent {
  @input
  itemPrefab!: ObjectPrefab;
  @input
  serviceModule!: RemoteServiceModule;
  private json: Array<qapair>;
  private delayedEvent: DelayedCallbackEvent;
  private testJson: Array<qapair> = [
    {
      question:
        "What is the significance of transitioning into a discussion about statistics and probabilities immediately after the introduction?",
      answer:
        "The instructor is transitioning to a discussion of statistics and probabilities, which suggests this topic will be important for understanding the subsequent material, potentially related to the 'Liz' persona or later activities.",
    },
    {
      question:
        "Why is it important to combine transcripts into a coherent segment when discussing statistics and probabilities?",
      answer:
        "Combining transcripts helps in identifying patterns and themes relevant to statistics and probabilities. A coherent segment will give context and highlight relationships within the data that might be missed if analyzing individual transcripts.",
    },
    {
      question:
        "How does pretending to be 'Liz' and mentioning a 'test' relate to the topic of statistics and probabilities?",
      answer:
        "It is unclear. The segment involves the instructor pretending to be 'Liz' saying the test will be good and then mentioning playing something, followed by a generic encouragement. The relation of this segment to statistics is unclear.",
    },
  ];

  onAwake(): void {
    this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
  }
  private getQuestions() {
    let httpRequest = RemoteServiceHttpRequest.create();
    httpRequest.url =
      "https://la-hacks-project.onrender.com/api/requestQuestions?snap_user_id=test_user&lecture_id=2e312afe-b903-4da3-959d-235e3e3f8fc6";
    httpRequest.method = RemoteServiceHttpRequest.HttpRequestMethod.Get;
    httpRequest.contentType = "application/json";

    this.serviceModule.performHttpRequest(httpRequest, (Response) => {
      if (Response.statusCode == 200) {
        this.json = JSON.parse(Response.body);
        print(Response.body);
        this.loadQuestions();
      }
    });
  }
  private repeatAction(var1: any) {
    // Your repeated action here
    var1.getQuestions(); // Call the function to get questions
    var1.delayedEvent.reset(1); // Reset the delayed event to repeat after 30 seconds

    // Schedule the next execution
  }

  private onStart() {
    this.delayedEvent = this.createEvent("DelayedCallbackEvent");
    this.delayedEvent.bind((eventData) => {
      this.repeatAction(this);
    });
    this.delayedEvent.reset(1); // 30 seconds delay
    this.loadQuestions();
  }

  private deleteInstances() {
    const children = this.getSceneObject().getChildrenCount();
    for (let i = children - 1; i > 0; i--) {
      const child = this.getSceneObject().getChild(i);
      child.destroy();
    }
  }

  private loadQuestions() {
    this.deleteInstances();
    print(this.json);
    const yStart = 0;
    const yOffset = -5.4;
    try {
      for (let i = 0; i < this.json.length; i++) {
        const item = this.itemPrefab.instantiate(this.getSceneObject());
        item.getChild(0).getComponent("Component.Text").text =
          this.json[i].question;
        (
          item.getChild(1).getComponent("Component.Script") as listItem
        ).answerStr = this.json[i].answer;
        const screenTransform = item.getComponent("Component.ScreenTransform");
        screenTransform.offsets.setCenter(new vec2(0, yStart + yOffset * i));
        item.enabled = true;
      }
    } catch (error) {
      print("Error loading questions: " + error);
    }
  }
}
