import {Heading} from '@react-spectrum/s2';
import {Route, Routes} from 'react-router-dom';

function FoundationScreen() {
  return (
    <main>
      <Heading level={1}>Área de trabalho</Heading>
    </main>
  );
}

export function App() {
  return (
    <Routes>
      <Route path="*" element={<FoundationScreen />} />
    </Routes>
  );
}
