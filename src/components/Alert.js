import React from 'react';

const Alert = ({ children, variant = 'default', title, description }) => {
  const variantClasses = {
    default: 'bg-blue-100 border-blue-500 text-blue-700',
    destructive: 'bg-red-100 border-red-500 text-red-700',
    success: 'bg-green-100 border-green-500 text-green-700',
  };

  return (
    <div className={`border-l-4 p-4 ${variantClasses[variant]}`} role="alert">
      {title && <p className="font-bold">{title}</p>}
      {description && <p>{description}</p>}
      {children}
    </div>
  );
};

const AlertTitle = ({ children }) => (
  <h3 className="font-medium mb-1">{children}</h3>
);

const AlertDescription = ({ children }) => (
  <p className="text-sm">{children}</p>
);

export { Alert, AlertTitle, AlertDescription };