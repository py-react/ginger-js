const useNavigate = () => {
  try {
    if (window !== undefined) {
      const customNavigate = (path, { replace = false } = {}) => {

        if (!path) {
          console.error('Navigation path is required');
          return;
        }
    
        if (typeof path !== 'string') {
          console.error('Navigation path must be a string');
          return;
        }
    
        if (replace) {
          window.location.replace(path);
        } else {
          window.location.href = path;
        }
    
        // Dispatch a popstate event to notify the app of the navigation
        window.dispatchEvent(new PopStateEvent('popstate'));
      };
    
      return customNavigate;
    }
  } catch (error) {
    // pass
    return ()=>{}
  }
};

export default useNavigate;