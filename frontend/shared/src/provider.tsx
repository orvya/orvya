import {Provider} from '@react-spectrum/s2/Provider';
import '@react-spectrum/s2/page.css';
import type {ReactNode} from 'react';
import {useHref, useNavigate, type NavigateOptions} from 'react-router-dom';

declare module '@react-spectrum/s2/Provider' {
  interface RouterConfig {
    routerOptions: NavigateOptions;
  }
}

export function OrvyaProvider({children}: {children: ReactNode}) {
  const navigate = useNavigate();
  return (
    <Provider locale="pt-BR" router={{navigate, useHref}}>
      {children}
    </Provider>
  );
}
