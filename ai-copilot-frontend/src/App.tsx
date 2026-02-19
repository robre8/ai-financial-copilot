import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import FileUpload from './components/FileUpload'

function App() {
  const [uploadCount, setUploadCount] = useState(0)

  return (
    <div>
      <ChatInterface key={uploadCount} />
      
      {/* Upload Modal/Sidebar */}
      <div className="fixed bottom-20 right-4 md:bottom-4 md:right-4 z-40 w-80">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
            📤 Subir Documento Financiero
          </h3>
          <FileUpload onUploadSuccess={() => setUploadCount(c => c + 1)} />
        </div>
      </div>
    </div>
  )
}

export default App

