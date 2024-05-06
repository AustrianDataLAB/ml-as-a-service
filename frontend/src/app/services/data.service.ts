import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {environment} from "../../environments/environment";

@Injectable({
    providedIn: 'root'
})
export class DataService {

    private global_url = environment.API_URL;
    private data_url = this.global_url + 'data'

    constructor(private http: HttpClient) {
    }

    uploadFile(file: File) {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(this.data_url, formData);
    }
}
