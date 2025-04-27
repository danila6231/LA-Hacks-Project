import { PinchButton } from "./SpectaclesInteractionKit/Components/UI/PinchButton/PinchButton";
import { setTimeout } from "./SpectaclesInteractionKit/Utils/FunctionTimingUtils";

@component
export class CaptionUI extends BaseScriptComponent {
  @input private text: Text;
  // @input private button: PinchButton;
  onAwake() {
    this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
    this.createEvent("UpdateEvent").bind(this.update.bind(this));
    // Set the text to be empty
    this.text.text = "";
  }
  private num: number = 0;
  private words: string[] = [];

  private update() {
    if (this.words.length > 50) {
      this.words = this.words.slice(1);
    }
    this.words.push("captions");
    // this.text.text = this.text.text.split(" ").slice(-50).join(" ");
    // this.text.text += `l captioners happening${this.num}`;
    this.num++;
  }

  private onStart() {
    // this.button.onButtonPinched.add(() => {
    // });
  }
}
