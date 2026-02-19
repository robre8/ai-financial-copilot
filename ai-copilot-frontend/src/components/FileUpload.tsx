import { useState } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

interface UploadProps {
  onUploadSuccess?: () => void;
}

export default function FileUpload({ onUploadSuccess }: UploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setError('⚠️ Por favor, sube solo archivos PDF');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      await axios.post(`${API_BASE}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setSuccess(`✅ ${file.name} subido y indexado correctamente`);
      onUploadSuccess?.();
      
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const errorMessage = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Error al subir el archivo';
      setError(`⚠️ ${errorMessage}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files?.[0]) {
      handleFile(files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition ${
          dragActive
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-slate-300 dark:border-slate-600 hover:border-blue-400'
        }`}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleChange}
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        <div className="pointer-events-none">
          {uploading ? (
            <>
              <div className="text-4xl mb-3">⏳</div>
              <p className="text-sm font-medium text-slate-900 dark:text-white">Subiendo...</p>
            </>
          ) : (
            <>
              <div className="text-4xl mb-3">📄</div>
              <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                Arrastra un PDF aquí o haz clic
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Máximo 50MB | Solo archivos PDF
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-200">{error}</p>
        </div>
      )}

      {success && (
        <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg animate-pulse">
          <p className="text-sm text-green-700 dark:text-green-200">{success}</p>
        </div>
      )}
    </div>
  );
}
