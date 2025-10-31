import React, { useEffect, useMemo, useState } from 'react';
import { GoogleMap, Marker, InfoWindow, useJsApiLoader } from '@react-google-maps/api';

type LatLng = { lat: number; lng: number };

type Clinic = {
  id: string;
  name: string;
  address: string;
  phone: string;
  latitude: number;
  longitude: number;
  hours?: string;
  bookingUrl?: string;
  distance_km?: number | null;
  insuranceAccepted?: string[];
  languagesSpoken?: string[];
};

interface ClinicMapProps {
  diagnosis?: any;
}

export const ClinicMap: React.FC<ClinicMapProps> = () => {
  const [userPosition, setUserPosition] = useState<LatLng | null>(null);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [selectedClinic, setSelectedClinic] = useState<Clinic | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => setUserPosition({ lat: 37.7749, lng: -122.4194 })
    );
  }, []);

  useEffect(() => {
    const fetchClinics = async () => {
      try {
        const qs = userPosition ? `?lat=${userPosition.lat}&lng=${userPosition.lng}&radius=50` : '';
        const res = await fetch(`/api/clinics${qs}`);
        const data = await res.json();
        setClinics(data.clinics || []);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Failed to load clinics', e);
      }
    };
    fetchClinics();
  }, [userPosition]);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: (import.meta as any).env.VITE_GOOGLE_MAPS_API_KEY || '',
  });

  const center = useMemo<LatLng>(() => userPosition || { lat: 37.7749, lng: -122.4194 }, [userPosition]);

  const handleReferralRequest = (clinic: Clinic) => {
    // TODO: integrate with referral backend / FHIR
    window.alert(`Referral request initiated for ${clinic.name}.`);
  };

  if (!isLoaded) return <div>Loading map...</div>;

  return (
    <div>
      <h4>Nearby Clinics and Specialists</h4>
      <GoogleMap zoom={12} center={center} mapContainerStyle={{ height: '400px', width: '100%' }}>
        {clinics.map((c) => (
          <Marker key={c.id} position={{ lat: c.latitude, lng: c.longitude }} onClick={() => setSelectedClinic(c)} />
        ))}
        {selectedClinic && (
          <InfoWindow position={{ lat: selectedClinic.latitude, lng: selectedClinic.longitude }} onCloseClick={() => setSelectedClinic(null)}>
            <div style={{ maxWidth: 240 }}>
              <h3 style={{ margin: 0 }}>{selectedClinic.name}</h3>
              <p style={{ margin: '4px 0' }}>{selectedClinic.address}</p>
              {selectedClinic.distance_km != null && <p style={{ margin: '4px 0' }}>Distance: {selectedClinic.distance_km} km</p>}
              <p style={{ margin: '4px 0' }}>Phone: {selectedClinic.phone}</p>
              {selectedClinic.hours && <p style={{ margin: '4px 0' }}>Hours: {selectedClinic.hours}</p>}
              <button className="btn-primary" onClick={() => handleReferralRequest(selectedClinic)}>Request Referral</button>
              {selectedClinic.bookingUrl && (
                <a className="btn-secondary" style={{ marginLeft: 8 }} href={selectedClinic.bookingUrl} target="_blank" rel="noreferrer">Book</a>
              )}
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
};

export default ClinicMap;


