import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class DataService {

  private global_url = environment.API_URL;
  private data_url = this.global_url + '/data'
  private training_url = this.global_url + '/training'
  private serving_url = this.global_url + '/serving'
  private inference_url = this.global_url + '/infer'


  constructor(private http: HttpClient) {
  }

  uploadFile(file: File) {
    console.log(this.data_url)
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(this.data_url, formData);
  }

  startTraining() {
    return this.http.post(this.training_url, {});
  }

  startServing() {
    return this.http.post(this.serving_url, {});
  }

  stopServing() {
    return this.http.delete(this.serving_url);
  }

  classify(image: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', image);
    return this.http.post(this.inference_url, formData, {responseType: 'text'});
  }

}
