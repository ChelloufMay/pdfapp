// src/main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';

import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, {
  // spread your existing providers and add animations provider
  providers: [
    ...appConfig.providers,
    provideAnimations(), // optional but useful for Material / smooth UI effects
  ]
}).catch((err) => console.error(err));

