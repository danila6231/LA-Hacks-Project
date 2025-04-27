/**
 * This class is responsible for creating and positioning grid content items based on a specified prefab and item count. It instantiates the items and arranges them vertically with a specified offset.
 */
@component
export class GridContentCreator extends BaseScriptComponent {
  @input
  itemPrefab!: ObjectPrefab;
  private sampleJson = {
    "qa-pair": [
      {
        question: "What is the capital of France?",
        answer:
          "The capital of France is Paris. It is the largest city in France and serves as the country's political, economic, and cultural center.",
      },
      {
        question: "How does photosynthesis work?",
        answer:
          "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen. The process takes place in the chloroplasts of plant cells, specifically using chlorophyll to capture light energy.",
      },
      {
        question: "What are the three laws of motion?",
        answer:
          "Newton's three laws of motion are: 1) An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force. 2) Force equals mass times acceleration (F=ma). 3) For every action, there is an equal and opposite reaction.",
      },
    ],
  };

  onAwake(): void {
    const yStart = 0;
    const yOffset = -5.4;

    for (let i = 0; i < this.sampleJson["qa-pair"].length; i++) {
      const item = this.itemPrefab.instantiate(this.getSceneObject());
      item.getChild(0).getComponent("Component.Text").text =
        this.sampleJson["qa-pair"][i].question;
      const screenTransform = item.getComponent("Component.ScreenTransform");
      screenTransform.offsets.setCenter(new vec2(0, yStart + yOffset * i));
      item.enabled = true;
    }
  }
}
