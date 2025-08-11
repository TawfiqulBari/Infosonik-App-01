import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  IconButton,
  Typography,
  Tooltip,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  MyLocation as MyLocationIcon,
  DirectionsWalk as WalkIcon,
  DirectionsCar as DriveIcon,
  DirectionsTransit as TransitIcon,
  Close as CloseIcon,
  Navigation as NavigationIcon,
  Speed as SpeedIcon,
  AttachMoney as MoneyIcon,
} from '@mui/icons-material';

// Google Maps Configuration
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || 'YOUR_API_KEY_HERE';

const GoogleMapRoute = ({ origin, destination, isFullscreen = false }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mapDialogOpen, setMapDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [routeData, setRouteData] = useState(null);
  const [mapError, setMapError] = useState(null);
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const directionsServiceRef = useRef(null);
  const directionsRendererRef = useRef(null);

  // Initialize Google Maps
  useEffect(() => {
    if (!window.google && GOOGLE_MAPS_API_KEY !== 'YOUR_API_KEY_HERE') {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = initializeMap;
      script.onerror = () => setMapError('Failed to load Google Maps');
      document.head.appendChild(script);
    } else if (window.google) {
      initializeMap();
    } else {
      // Fallback to mock mode
      setMapError('Google Maps API key not configured');
      setLoading(false);
    }
  }, [origin, destination]);

  const initializeMap = () => {
    if (!mapRef.current || !window.google) return;

    try {
      // Initialize map
      const map = new window.google.maps.Map(mapRef.current, {
        zoom: 13,
        center: { lat: 23.8103, lng: 90.4125 }, // Dhaka center
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: false,
      });

      mapInstanceRef.current = map;

      // Initialize directions service and renderer
      directionsServiceRef.current = new window.google.maps.DirectionsService();
      directionsRendererRef.current = new window.google.maps.DirectionsRenderer({
        draggable: true,
        panel: null,
      });

      directionsRendererRef.current.setMap(map);

      // Calculate route if both locations are provided
      if (origin && destination) {
        calculateRoute();
      } else {
        setLoading(false);
      }

      // Add click listener for current location
      const locationButton = document.createElement('button');
      locationButton.textContent = 'My Location';
      locationButton.classList.add('custom-map-control-button');
      locationButton.style.cssText = `
        background: white;
        border: 2px solid #fff;
        border-radius: 3px;
        box-shadow: 0 2px 6px rgba(0,0,0,.3);
        cursor: pointer;
        float: right;
        margin: 8px;
        padding: 0 8px;
        text-align: center;
        font-family: Roboto,Arial,sans-serif;
        font-size: 16px;
        line-height: 38px;
        color: rgb(25,25,25);
      `;

      locationButton.addEventListener('click', () => {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              const pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
              };
              map.setCenter(pos);
              map.setZoom(15);
              
              new window.google.maps.Marker({
                position: pos,
                map: map,
                title: 'Your Location',
                icon: {
                  path: window.google.maps.SymbolPath.CIRCLE,
                  scale: 8,
                  fillColor: '#4285F4',
                  fillOpacity: 1,
                  strokeColor: 'white',
                  strokeWeight: 2,
                }
              });
            },
            () => {
              console.error('Error: The Geolocation service failed.');
            }
          );
        } else {
          console.error('Error: Your browser doesn\'t support geolocation.');
        }
      });

      map.controls[window.google.maps.ControlPosition.TOP_RIGHT].push(locationButton);

    } catch (error) {
      console.error('Map initialization error:', error);
      setMapError('Failed to initialize map');
      setLoading(false);
    }
  };

  const calculateRoute = async () => {
    if (!directionsServiceRef.current || !origin || !destination) {
      setLoading(false);
      return;
    }

    setLoading(true);
    
    try {
      const result = await new Promise((resolve, reject) => {
        directionsServiceRef.current.route(
          {
            origin: origin,
            destination: destination,
            travelMode: window.google.maps.TravelMode.DRIVING,
            unitSystem: window.google.maps.UnitSystem.METRIC,
            avoidHighways: false,
            avoidTolls: false,
          },
          (result, status) => {
            if (status === 'OK') {
              resolve(result);
            } else {
              reject(new Error(`Directions request failed: ${status}`));
            }
          }
        );
      });

      // Display route
      directionsRendererRef.current.setDirections(result);

      // Extract route information
      const route = result.routes[0];
      const leg = route.legs[0];
      
      // Calculate estimated cost based on distance (rough estimation for Bangladesh)
      const distanceKm = leg.distance.value / 1000;
      const estimatedCostBDT = Math.round(distanceKm * 15); // Rough estimate: 15 BDT per km

      setRouteData({
        distance: leg.distance.text,
        duration: leg.duration.text,
        estimatedCost: `৳${estimatedCostBDT}`,
        startAddress: leg.start_address,
        endAddress: leg.end_address,
        distanceValue: leg.distance.value,
        durationValue: leg.duration.value,
      });

    } catch (error) {
      console.error('Route calculation error:', error);
      setMapError('Failed to calculate route');
    } finally {
      setLoading(false);
    }
  };

  const handleFullscreenToggle = () => {
    setMapDialogOpen(!mapDialogOpen);
  };

  // Fallback component for when Google Maps is not available
  const FallbackMap = ({ message }) => (
    <Paper
      sx={{
        height: isFullscreen ? 400 : 250,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(45deg, #e8f5e8 25%, #f0f8ff 25%, #f0f8ff 50%, #e8f5e8 50%, #e8f5e8 75%, #f0f8ff 75%, #f0f8ff)',
        backgroundSize: '20px 20px',
        border: '2px dashed #ccc',
        position: 'relative',
      }}
    >
      <Box textAlign="center" sx={{ p: 3 }}>
        <NavigationIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom color="text.secondary">
          Interactive Map
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="primary" gutterBottom>
            📍 From: {origin || 'Not specified'}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1, mb: 1 }}>
            ↓ Route visualization
          </Typography>
          <Typography variant="body2" color="secondary">
            📍 To: {destination || 'Not specified'}
          </Typography>
        </Box>
        
        {routeData && (
          <Box sx={{ mb: 2 }}>
            <Chip 
              icon={<SpeedIcon />}
              label={routeData.distance}
              size="small"
              color="primary"
              sx={{ mr: 1, mb: 1 }}
            />
            <Chip 
              icon={<DriveIcon />}
              label={routeData.duration}
              size="small"
              color="secondary"
              sx={{ mr: 1, mb: 1 }}
            />
            <Chip 
              icon={<MoneyIcon />}
              label={routeData.estimatedCost}
              size="small"
              color="success"
              sx={{ mb: 1 }}
            />
          </Box>
        )}
        
        <Typography variant="caption" color="text.secondary">
          {message}
        </Typography>
      </Box>
    </Paper>
  );

  if (!origin && !destination) {
    return (
      <Alert severity="info">
        Enter origin and destination to view route
      </Alert>
    );
  }

  // Show fallback for configuration or error cases
  if (mapError || GOOGLE_MAPS_API_KEY === 'YOUR_API_KEY_HERE') {
    return <FallbackMap message={mapError || "Configure Google Maps API key to enable interactive maps"} />;
  }

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Route Information Bar */}
      {routeData && (
        <Box sx={{ mb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip 
            icon={<SpeedIcon />}
            label={routeData.distance}
            size="small"
            color="primary"
          />
          <Chip 
            icon={<DriveIcon />}
            label={routeData.duration}
            size="small"
            color="secondary"
          />
          <Chip 
            icon={<MoneyIcon />}
            label={`Est. ${routeData.estimatedCost}`}
            size="small"
            color="success"
          />
        </Box>
      )}

      {/* Map Container */}
      <Paper
        sx={{
          height: isFullscreen ? 400 : 250,
          width: '100%',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Loading Overlay */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'rgba(255, 255, 255, 0.8)',
              zIndex: 10,
            }}
          >
            <Box textAlign="center">
              <CircularProgress sx={{ mb: 2 }} />
              <Typography>Loading route...</Typography>
            </Box>
          </Box>
        )}

        {/* Map Controls */}
        <Box
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
            zIndex: 5,
          }}
        >
          <Tooltip title="Fullscreen Map">
            <IconButton
              size="small"
              onClick={handleFullscreenToggle}
              sx={{ 
                bgcolor: 'background.paper', 
                '&:hover': { bgcolor: 'grey.100' },
                boxShadow: 1,
              }}
            >
              <FullscreenIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Actual Google Maps Container */}
        <div
          ref={mapRef}
          style={{
            width: '100%',
            height: '100%',
          }}
        />
      </Paper>

      {/* Fullscreen Map Dialog */}
      <Dialog
        open={mapDialogOpen}
        onClose={() => setMapDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        fullScreen={isMobile}
        PaperProps={{
          sx: {
            height: isMobile ? '100vh' : '80vh',
          }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Route: {origin} → {destination}
          </Typography>
          <IconButton onClick={() => setMapDialogOpen(false)}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ p: 0, height: '100%' }}>
          {routeData && (
            <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  icon={<SpeedIcon />}
                  label={routeData.distance}
                  color="primary"
                />
                <Chip 
                  icon={<DriveIcon />}
                  label={routeData.duration}
                  color="secondary"
                />
                <Chip 
                  icon={<MoneyIcon />}
                  label={`Est. ${routeData.estimatedCost}`}
                  color="success"
                />
              </Box>
            </Box>
          )}
          
          <Box sx={{ height: 'calc(100% - 80px)', position: 'relative' }}>
            {loading && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'rgba(255, 255, 255, 0.8)',
                  zIndex: 10,
                }}
              >
                <CircularProgress />
              </Box>
            )}
            
            <div
              style={{
                width: '100%',
                height: '100%',
              }}
              ref={(el) => {
                if (el && mapDialogOpen) {
                  // Re-initialize map for dialog
                  setTimeout(() => {
                    if (window.google) {
                      const dialogMap = new window.google.maps.Map(el, {
                        zoom: 13,
                        center: { lat: 23.8103, lng: 90.4125 },
                        mapTypeControl: true,
                        streetViewControl: true,
                        fullscreenControl: true,
                      });

                      const dialogDirectionsRenderer = new window.google.maps.DirectionsRenderer();
                      dialogDirectionsRenderer.setMap(dialogMap);

                      if (directionsRendererRef.current && directionsRendererRef.current.getDirections()) {
                        dialogDirectionsRenderer.setDirections(directionsRendererRef.current.getDirections());
                      }
                    }
                  }, 100);
                }
              }}
            />
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default GoogleMapRoute;
