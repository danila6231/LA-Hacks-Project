@component
export class CaptionUI extends BaseScriptComponent {
  @input
  private text: Text;
  @input
  serviceModule!: RemoteServiceModule;
  private delayedEvent: DelayedCallbackEvent;
  onAwake() {
    this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
    // Set the text to be empty
    this.text.text = "";
  }
  private num: number = 0;

  private getCaptions() {
    let httpRequest = RemoteServiceHttpRequest.create();
    httpRequest.url =
      "https://la-hacks-project.onrender.com/api/getAndClearTranscripts?snap_user_id=test_user&lecture_id=2e312afe-b903-4da3-959d-235e3e3f8fc6";
    httpRequest.method = RemoteServiceHttpRequest.HttpRequestMethod.Post;
    httpRequest.body = JSON.stringify({
      snap_user_id: "test_user",
      lecture_id: "2e312afe-b903-4da3-959d-235e3e3f8fc6",
    });
    httpRequest.contentType = "application/json";

    this.serviceModule.performHttpRequest(httpRequest, (Response) => {
      if (Response.statusCode == 200) {
        if (Response.body != '""') {
          this.text.text = Response.body;
        }
        print(Response.body);
      }
    });
  }

  private repeatAction(var1: any) {
    // Your repeated action here
    var1.getCaptions(); // Call the function to get questions
    var1.delayedEvent.reset(1); // Reset the delayed event to repeat after 30 seconds

    // Schedule the next execution
  }

  private onStart() {
    this.delayedEvent = this.createEvent("DelayedCallbackEvent");
    this.delayedEvent.bind((eventData) => {
      this.repeatAction(this);
    });
    this.delayedEvent.reset(1); // 30 seconds delay
  }
}
