export type Bounds = [number, number, number, number];

export type ViewState = {
  longitude: number;
  latitude: number;
  zoom: number;
  pitch?: number;
  bearing?: number;
};

export type VisualizationLayer = {
  id: string;
  type: string;
  visible: boolean;
  opacity: number;
  source: Record<string, unknown>;
  style: Record<string, unknown>;
};

export interface MapController {
  setView(view: ViewState): void;
  fitBounds(bounds: Bounds): void;
  addLayer(layer: VisualizationLayer): void;
  removeLayer(layerId: string): void;
  setLayerVisibility(layerId: string, visible: boolean): void;
}
