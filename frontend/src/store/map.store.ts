
import { create } from "zustand";

interface MapState {
  selectedLatitude: number | null;
  selectedLongitude: number | null;
  selectedArea: GeoJSON.Polygon | null;

  setSelectedLocation: (latitude: number, longitude: number) => void;
  setSelectedArea: (area: GeoJSON.Polygon | null) => void;
}

export const useMapStore = create<MapState>((set) => ({
  selectedLatitude: null,
  selectedLongitude: null,
  selectedArea: null,

  setSelectedLocation: (latitude, longitude) =>
    set({
      selectedLatitude: latitude,
      selectedLongitude: longitude,
    }),

  setSelectedArea: (area) =>
    set({
      selectedArea: area,
    }),
}));
