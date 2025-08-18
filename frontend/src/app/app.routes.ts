import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => {
      // @ts-ignore
      return import("./pages/home/home.component").then(m => m.HomeComponent);
    }
  }];
