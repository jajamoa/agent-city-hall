// Screen breakpoints (in pixels)
const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 1024,
  DESKTOP: 1024
};

// Device type detection using User Agent
const checkDeviceType = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  const isMobileUA = /iphone|ipad|ipod|android|blackberry|windows phone/i.test(userAgent);
  const isTabletUA = /(ipad|tablet|playbook|silk)|(android(?!.*mobile))/i.test(userAgent);
  
  return {
    isMobileUA,
    isTabletUA
  };
};

export const isMobileDevice = () => {
  // Combine screen size and device type detection
  const { isMobileUA } = checkDeviceType();
  const isMobileWidth = window.innerWidth <= BREAKPOINTS.MOBILE;
  
  // Consider it mobile if either condition is true
  return isMobileWidth || isMobileUA;
};

export const isTabletDevice = () => {
  // Combine screen size and device type detection
  const { isTabletUA } = checkDeviceType();
  const isTabletWidth = window.innerWidth > BREAKPOINTS.MOBILE && window.innerWidth <= BREAKPOINTS.TABLET;
  
  // Consider it tablet if either condition is true
  return isTabletWidth || isTabletUA;
};

export const getDeviceType = () => {
  // Return device type based on combined checks
  if (isMobileDevice()) return 'mobile';
  if (isTabletDevice()) return 'tablet';
  return 'desktop';
}; 