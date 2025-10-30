import { useState, useCallback } from 'react';

interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}

export const useForm = (initialValues: Record<string, any> = {}) => {
  const [formState, setFormState] = useState<FormState>({
    values: initialValues,
    errors: {},
    touched: {},
    isSubmitting: false,
  });

  const setValue = useCallback((name: string, value: any) => {
    setFormState(prev => ({
      ...prev,
      values: { ...prev.values, [name]: value },
      errors: { ...prev.errors, [name]: '' },
    }));
  }, []);

  const setTouched = useCallback((name: string) => {
    setFormState(prev => ({
      ...prev,
      touched: { ...prev.touched, [name]: true },
    }));
  }, []);

  const setError = useCallback((name: string, error: string) => {
    setFormState(prev => ({
      ...prev,
      errors: { ...prev.errors, [name]: error },
    }));
  }, []);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormState(prev => ({
        ...prev,
        values: {
          ...prev.values,
          [name]: checked
            ? [...(prev.values[name] || []), value]
            : (prev.values[name] || []).filter((v: string) => v !== value)
        }
      }));
    } else {
      setValue(name, value);
    }
  }, [setValue]);

  const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setTouched(e.target.name);
  }, [setTouched]);

  const validateField = useCallback((name: string, value: any) => {
    let error = '';

    switch (name) {
      case 'email':
        if (!value) {
          error = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          error = 'Please enter a valid email address';
        }
        break;
      case 'name':
        if (!value) {
          error = 'Name is required';
        } else if (value.length < 2) {
          error = 'Name must be at least 2 characters';
        }
        break;
      case 'message':
        if (!value) {
          error = 'Message is required';
        } else if (value.length < 10) {
          error = 'Message must be at least 10 characters';
        }
        break;
      default:
        break;
    }

    if (error) {
      setError(name, error);
    } else {
      setError(name, '');
    }

    return !error;
  }, [setError]);

  const validateForm = useCallback(() => {
    let isValid = true;
    Object.keys(formState.values).forEach(key => {
      const fieldValid = validateField(key, formState.values[key]);
      if (!fieldValid) {
        isValid = false;
      }
    });
    return isValid;
  }, [formState.values, validateField]);

  const handleSubmit = useCallback(async (onSubmit: (values: Record<string, any>) => Promise<void> | void) => {
    setFormState(prev => ({ ...prev, isSubmitting: true }));

    if (validateForm()) {
      try {
        await onSubmit(formState.values);
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Form submission error:', error);
      }
    }

    setFormState(prev => ({ ...prev, isSubmitting: false }));
  }, [formState.values, validateForm]);

  const resetForm = useCallback(() => {
    setFormState({
      values: initialValues,
      errors: {},
      touched: {},
      isSubmitting: false,
    });
  }, [initialValues]);

  return {
    values: formState.values,
    errors: formState.errors,
    touched: formState.touched,
    isSubmitting: formState.isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setValue,
    resetForm,
    validateField,
  };
};


