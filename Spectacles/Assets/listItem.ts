import { PinchButton } from "./SpectaclesInteractionKit/Components/UI/PinchButton/PinchButton";

@component
export class listItem extends BaseScriptComponent {
  @input
  answerText: Text;
  @input
  pinchButton: PinchButton;
  public answerStr: string;
  onAwake() {
    this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
  }

  private onStart() {
    this.pinchButton.onButtonPinched.add(() => {
      this.answerText.text = this.answerStr;
    });
  }
}
