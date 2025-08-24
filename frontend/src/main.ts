// main.ts
// Bootstraps the standalone AppComponent and applies the global appConfig providers.
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, {
  providers: [
    ...appConfig.providers,
    provideAnimations()
  ]
}).catch(err => console.error(err));


