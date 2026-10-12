import React, { useState, type ChangeEvent } from "react";
import type { UserDTO } from "../../models/user/UserDTO";
import type { UpdateProfileDTO } from "../../models/user/UpdateProfileDTO";
import { ProfileAvatar } from "./ProfileAvatar";

interface ProfileEditFormProps {
  user: UserDTO;
  profileImageUrl: string | null;
  onSave: (data: UpdateProfileDTO, imageFile: File | null) => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  dateOfBirth: string;
  gender: string;
  country: string;
  street: string;
  number: string;
}

export const ProfileEditForm: React.FC<ProfileEditFormProps> = ({
  user,
  profileImageUrl,
  onSave,
  onCancel,
  isLoading,
}) => {
  const [formData, setFormData] = useState<FormData>({
    firstName: user.firstName || "",
    lastName: user.lastName || "",
    email: user.email || "",
    password: "",
    dateOfBirth: user.dateOfBirth ? user.dateOfBirth.slice(0, 10) : "",
    gender: user.gender || "",
    country: user.country || "",
    street: user.street || "",
    number: user.streetNumber || "",
  });

  const [newImage, setNewImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleImageChange = (file: File) => {
    setNewImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const updateData: UpdateProfileDTO = {
      first_name: formData.firstName,
      last_name: formData.lastName,
      email: formData.email,
      date_of_birth: formData.dateOfBirth,
      gender: formData.gender,
      country: formData.country,
      street: formData.street,
      street_number: formData.number,
    };

    if (formData.password.trim()) {
      updateData.password = formData.password;
    }

    await onSave(updateData, newImage);
  };

  const inputClass = `w-full bg-white/50 px-4 py-3 rounded-xl border border-gray-200
                      focus:border-violet-400 focus:ring-2 focus:ring-violet-100
                      outline-none transition-all duration-200 placeholder:text-gray-400`;

  const labelClass = "block text-sm font-medium text-gray-700 mb-2";

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl border border-white/50 overflow-hidden">
      {/* Header */}
      <div className="relative h-32 bg-gradient-to-r from-violet-500 via-purple-500 to-indigo-500">
        <div className="absolute -bottom-16 left-1/2 -translate-x-1/2">
          <ProfileAvatar
            imageUrl={imagePreview || profileImageUrl}
            firstName={formData.firstName}
            lastName={formData.lastName}
            size="lg"
            editable={true}
            onImageChange={handleImageChange}
          />
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="pt-20 p-6">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          Edit Profile
        </h2>

        {newImage && (
          <p className="text-center text-sm text-violet-600 mb-4">
            ✓ New image selected: {newImage.name}
          </p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* First Name */}
          <div>
            <label className={labelClass}>First Name</label>
            <input
              type="text"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter first name"
              required
            />
          </div>

          {/* Last Name */}
          <div>
            <label className={labelClass}>Last Name</label>
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter last name"
              required
            />
          </div>

          {/* Email */}
          <div className="md:col-span-2">
            <label className={labelClass}>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter email"
              required
            />
          </div>

          {/* Password */}
          <div className="md:col-span-2">
            <label className={labelClass}>
              New Password
              <span className="text-gray-400 font-normal ml-2">(leave empty to keep current)</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`${inputClass} pr-20`}
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-medium
                           text-violet-500 hover:text-violet-700 transition-colors cursor-pointer"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* Date of Birth */}
          <div>
            <label className={labelClass}>Date of Birth</label>
            <input
              type="date"
              name="dateOfBirth"
              value={formData.dateOfBirth}
              onChange={handleChange}
              max={new Date().toISOString().split("T")[0]}
              className={inputClass}
            />
          </div>

          {/* Gender */}
          <div>
            <label className={labelClass}>Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className={`${inputClass} cursor-pointer`}
            >
              <option value="">Select gender...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Country */}
          <div>
            <label className={labelClass}>Country</label>
            <input
              type="text"
              name="country"
              value={formData.country}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter country"
            />
          </div>

          {/* Street */}
          <div>
            <label className={labelClass}>Street</label>
            <input
              type="text"
              name="street"
              value={formData.street}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter street"
            />
          </div>

          {/* Street Number */}
          <div>
            <label className={labelClass}>Number</label>
            <input
              type="text"
              name="number"
              value={formData.number}
              onChange={handleChange}
              className={inputClass}
              placeholder="Enter number"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mt-8">
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 py-3 px-6 rounded-xl font-semibold
                       bg-gray-100 hover:bg-gray-200 text-gray-700
                       transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 py-3 px-6 rounded-xl font-semibold
                       bg-gradient-to-r from-violet-500 to-indigo-500 
                       hover:from-violet-600 hover:to-indigo-600
                       text-white shadow-lg hover:shadow-xl
                       transition-all duration-300
                       disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center justify-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M5 13l4 4L19 7" />
                </svg>
                Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};