import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import {DataService} from "../services/data.service";
import {ToastrService} from "ngx-toastr";

@Component({
  selector: 'app-waiting-game',
  templateUrl: './waiting-game.component.html',
  styleUrls: ['./waiting-game.component.css']
})
export class WaitingGameComponent implements AfterViewInit {
  @ViewChild('dino', { static: false }) dino!: ElementRef;
  @ViewChild('cactus', { static: false }) cactus!: ElementRef;
  isAlive = true;

  ngAfterViewInit() {
    document.addEventListener('keydown', () => this.startGame());
  }

  startGame() {
    if (this.isAlive) {
      this.jump();
      this.checkAlive();
    }
  }

  jump() {
    if (this.dino.nativeElement.classList != "jump") {
      this.dino.nativeElement.classList.add("jump");
      setTimeout(() => {
        this.dino.nativeElement.classList.remove("jump");
      }, 300);
    }
  }

  checkAlive() {
    let checkAliveInterval = setInterval(() => {
      let dinoTop = parseInt(window.getComputedStyle(this.dino.nativeElement).getPropertyValue("top"));
      let cactusLeft = parseInt(window.getComputedStyle(this.cactus.nativeElement).getPropertyValue("left"));

      if (cactusLeft > 0 && cactusLeft < 70 && dinoTop >= 143) {
        this.dino.nativeElement.style.animationPlayState = "paused";
        this.cactus.nativeElement.style.animationPlayState = "paused";
        this.isAlive = false;
        clearInterval(checkAliveInterval);
      }
    }, 10);
  }

  resetGame() {
    this.isAlive = true;

    // Pause animations
    this.dino.nativeElement.style.animationPlayState = 'paused';
    this.cactus.nativeElement.style.animationPlayState = 'paused';

    // Reset positions
    this.dino.nativeElement.style.top = '143px';
    this.cactus.nativeElement.style.left = '600px';

    // Remove the cactus animation class to reset it
    this.cactus.nativeElement.style.animation = 'none';

    // Force reflow (repaint) to restart the animation
    void this.cactus.nativeElement.offsetWidth;

    // Add the animation back
    this.cactus.nativeElement.style.animation = '';

    // Restart animations
    this.dino.nativeElement.style.animationPlayState = 'running';
    this.cactus.nativeElement.style.animationPlayState = 'running';

    // Restart the checkAlive interval
    this.checkAlive();
  }
}
