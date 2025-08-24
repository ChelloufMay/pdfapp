// app.routes.ts
// Root route configuration: lazy-load the Home component (standalone).
import { Route } from '@angular/router';

export const routes: Route[] = [
  {
    path: '',
    loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent)
  }
];

