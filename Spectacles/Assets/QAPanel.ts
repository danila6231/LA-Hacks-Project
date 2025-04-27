import { ContainerFrame } from "./SpectaclesInteractionKit/Components/UI/ContainerFrame/ContainerFrame";
import { PinchButton } from "./SpectaclesInteractionKit/Components/UI/PinchButton/PinchButton";

// Global tweenManager
declare var tweenManager: any;

@component
export class QAPanel extends BaseScriptComponent {
    @input private frame: ContainerFrame;
    @input private content: SceneObject;
    @input private bottom: SceneObject;
    //@input private button: PinchButton;

    // Toggle state
    private state : boolean = true;
    public lerp : number = 1.0;

    onAwake() {
        // Starting size
        this.frame.innerSize = new vec2(30, 35);
        this.content.getTransform().setLocalPosition(new vec3(0,7.5,0));
        this.bottom.enabled = true;

        // Attach animation handlers
        this.createEvent("OnStartEvent").bind(this.onStart.bind(this));
        this.createEvent("UpdateEvent").bind(this.update.bind(this));
    }

    update(){
        this.lerpOutput();
    }

    private lerpFunction(start : number, end : number, val : number) : number{
        return (end - start) * val + start;
    }

    public lerpOutput(){
        if (this.lerp == 0.0){
            this.bottom.enabled = false;
        }
        else {
            this.bottom.enabled = true;
        }
        this.frame.innerSize = new vec2(30, this.lerpFunction(20, 35, this.lerp));
        this.content.getTransform().setLocalPosition(new vec3(0, this.lerpFunction(0, 7.5, this.lerp), 0.0));
    }

    public enableBottom(){
        this.frame.innerSize = new vec2(30, 35);
        this.content.getTransform().setLocalPosition(new vec3(0,7.5,0));
        this.bottom.enabled = true;
        /*print("Tweening in...");
        tweenManager.setEndValue(this.bottom, "answersDrawerTween", 1.0);
        tweenManager.startTween(this.bottom, "answersDrawerTween", this.enableBottom);*/
    }

    public disableBottom(){
        /*this.frame.innerSize = new vec2(30, 20);
        this.content.getTransform().setLocalPosition(new vec3(0,0,0));
        this.bottom.enabled = false;*/
        /*print("Tweening out...");
        tweenManager.setEndValue(this.bottom, "answersDrawerTween", 0.0);
        tweenManager.startTween(this.bottom, "answersDrawerTween", this.disableBottom);*/
    }

    private onStart(){
        // On action change
        /*this.button.onButtonPinched.add(() => {
            this.state = !this.state;
            if (this.state){
                //this.enableBottom();
                print("Tweening in...");
                tweenManager.setEndValue(this.bottom, "answersDrawerTween", 1.0);
                tweenManager.startTween(this.bottom, "answersDrawerTween", () => {});
            }
            else {
                //this.disableBottom();
                print("Tweening out...");
                tweenManager.setEndValue(this.bottom, "answersDrawerTween", 0.0);
                tweenManager.startTween(this.bottom, "answersDrawerTween", () => {});
            }
        });*/
    }
}
