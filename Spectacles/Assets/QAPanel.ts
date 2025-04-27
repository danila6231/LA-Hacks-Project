import { ContainerFrame } from "./SpectaclesInteractionKit/Components/UI/ContainerFrame/ContainerFrame";

@component
export class QAPanel extends BaseScriptComponent {
    @input private frame: ContainerFrame;
    @input private content: SceneObject;

    onAwake() {
        // Attach animation handlers
        
    }

    private onStart(){
        // Starting size
        this.frame.innerSize = new vec2(30, 20);
        this.content.getTransform().setLocalPosition(new vec3(0,0,0));

        // On action change 
        
    }
}
