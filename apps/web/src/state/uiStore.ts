import { create } from "zustand";

export type MapMode = "2d" | "3d";

type UiState = {
  mode: MapMode;
  setMode: (mode: MapMode) => void;
};

export const useUiStore = create<UiState>((set) => ({
  mode: "2d",
  setMode: (mode) => set({ mode }),
}));
