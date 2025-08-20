import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: async () => {
      const m = await import("./pages/home/home.component");
      return m.HomeComponent;
    }
  }];
