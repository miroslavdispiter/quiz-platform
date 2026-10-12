export interface UpdateProfileDTO {
  first_name?: string;
  last_name?: string;
  email?: string;
  date_of_birth?: string; // "YYYY-MM-DD"
  password?: string;
  gender?: string;
  country?: string;
  street?: string;
  street_number?: string;
}