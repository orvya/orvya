import {Heading} from '@react-spectrum/s2';
import {Route, Routes} from 'react-router-dom';

function FoundationScreen() {
  return (
    <main>
      <Heading level={1}>Administração da Plataforma</Heading>
    </main>
  );
}

export function AdminApp() {
  return (
    <Routes>
      <Route path="*" element={<FoundationScreen />} />
    </Routes>
  );
}
