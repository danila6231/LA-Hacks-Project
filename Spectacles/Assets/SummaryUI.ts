@component
export class SummaryUI extends BaseScriptComponent {
  @input
  text: Text;
  @input
  serviceModule!: RemoteServiceModule;
  private delayedEvent: DelayedCallbackEvent;

  onAwake() {
    this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
  }

  private getSummary() {
    let httpRequest = RemoteServiceHttpRequest.create();
    httpRequest.url =
      "https://la-hacks-project.onrender.com/api/requestSummary?snap_user_id=Test_User&lecture_id=ff9f8362-dada-437c-bb43-c59a1dee43c1";
    httpRequest.method = RemoteServiceHttpRequest.HttpRequestMethod.Get;
    httpRequest.contentType = "application/json";

    this.serviceModule.performHttpRequest(httpRequest, (Response) => {
      if (Response.statusCode == 200) {
        this.text.text = JSON.parse(Response.body).text;
        // print(Response.body);
      }
    });
  }

  private repeatAction(var1: any) {
    // Your repeated action here
    var1.getSummary(); // Call the function to get questions
    var1.delayedEvent.reset(15); // Reset the delayed event to repeat after 30 seconds

    // Schedule the next execution
  }

  private onStart() {
    this.delayedEvent = this.createEvent("DelayedCallbackEvent");
    this.delayedEvent.bind((eventData) => {
      this.repeatAction(this);
    });
    this.delayedEvent.reset(15); // 30 seconds delay
  }
}
